ffprobe /tmp/output.mp4 -show_frames
ffplay -debug mb_type -flags2 +export_mvs /tmp/output.mp4 -vf codecview=mv=pf+bf+bb
