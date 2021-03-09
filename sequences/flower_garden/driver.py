prefix = "/tmp/"
_input = prefix + "original"
_output = prefix + "output"
n_frames = 5

for i in range(n_frames):
    with open(f"{_input}_{i:03d}.png", "rb") as f_input, open(f"/tmp/pipe", "wb") as f_output:
        input()
        print(".")
        while (byte := f_input.read(1)):
            f_output.write(byte)
            f_output.flush()
