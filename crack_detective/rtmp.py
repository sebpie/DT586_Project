import argparse
import ffmpeg
import os

def get_crop_kwargs(args):
    kwargs = {'x': args.crop_x,
              'y': args.crop_y,
              "width": args.width or 640,
              "height": args.height or 480,
            }

    match(args.scan):
        case "static":
            if args.x:
                kwargs['x'] = args.x
            if args.y:
                kwargs['y'] = args.y

        case "bounce":
            kwargs['x'] = f"""
                            if(eq(mod(floor(st(8,t*{args.sliding_speed})/(iw - out_w)),2),0),
                            mod(ld(8),iw - out_w),
                            iw - out_w-mod(ld(8), iw - out_w))
                        """
            kwargs['y'] = f"""
                            if(eq(mod(floor(st(9,t*{args.sliding_speed})/(ih - out_h)),2),0),
                            mod(ld(9),ih - out_h),
                            ih-h-mod(ld(9), ih - out_h))
                        """

        case "horizontal":
            kwargs['x'] = f"""
                            if(eq(mod(floor(st(8,t*{args.sliding_speed})/(iw - out_w)),2),0),
                            mod(ld(8),iw - out_w)
                            iw - out_w-mod(ld(8), iw - out_w))
                        """

        case "vertical":
            kwargs['y'] = f"""
                            if(eq(mod(floor(st(9,t*{args.sliding_speed})/(ih - out_h)),2),0),
                            mod(ld(9),ih - out_h),
                            ih-h-mod(ld(9), ih - out_h))
                        """
    return kwargs


def parse_args():
    parser = argparse.ArgumentParser(
        prog="rtmp",
        description="Simple CLI tool to stream video from a picture",
        epilog="")

    parser.add_argument("input_file", nargs=1, help="Filename for the image source.")
    parser.add_argument("url", nargs='?', default="rtmp://localhost:8000/live", help="Destination URL for the RTMP stream (e.g. \"rtmp://localhost:9135/live\").")
    parser.add_argument("--width", type=int, default=1280, help="Width in pixel of the cropping window and output of the stream.")
    parser.add_argument("--height", type=int, default=720, help="Height in pixel of the cropping window and output stream.")
    parser.add_argument("--crop_x", type=int, default=0, help="The horizontal position, in the input file, of the left edge of the output video.")
    parser.add_argument("--crop_y", type=int, default=0, help="The vertical position, in the input file, of the top edge of the output video.")
    parser.add_argument("--scan", choices=["bounce", "horizontal", "vertical", "static"])
    parser.add_argument("--sliding_speed", default=100, type=int, help="Speed at which the cropping window moves across the input image.")
    parser.add_argument("--ffmpeg_path", default=os.environ.get("FFMPEG_BINARY", None), help="Path to ffmpeg binary.")
    parser.add_argument("--pix_fmt", default="bgr24", help="Pixel format for output stream.")
    parser.add_argument("--fps", default=30, type=int, help="Frame rate of the output stream.")
    return parser.parse_args()


def main(args=None):

    ffmpeg_args = { }
    if args.ffmpeg_path:
        ffmpeg_args["cmd"] = args.ffmpeg_path

    kwargs = get_crop_kwargs(args)

    return (
        ffmpeg
        .input(args.input_file[0], loop=1)
        .crop(**kwargs)
        .filter("fps", fps=args.fps, round="up")
        .output(args.url,
                format='flv',
                pix_fmt=args.pix_fmt,
                s=f'{args.width}x{args.height}')
        .run(**ffmpeg_args)
    )
if __name__ == '__main__':
    args = parse_args()
    print(args)
    main(args)