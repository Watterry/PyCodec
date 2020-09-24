# PyCodec

Using Python to do some codec mathematics.

If you are interesting in any module of video coding standards, you can request the part to me and I will find some time to realize it.

# Why using Python?

This library just do basic algorithm analysis and don't care about speed. The aim of using Python, the first is just for fun, the second is just to familiar Video Coding standards with high level language. By using Python, we can just focus on the theory of video coding. When we read code like x264 or x265, there are too many languange details mixing up with video coding standards which make the code poor to read.

There is another advantage using Python to do theoretic research. It is very convenient to do unit test in seperate file. For example, you can do CAVLC by just reading the code and do some test using example from the book. It is very convinent to change the test data directly from Python file.

# Dependency

[h26x-extractor](https://github.com/slhck/h26x-extractor)

```bash
pip3 install h26x-extractor
```

If we can't install h26x-extractor by the pip3 command, we can also download the package from Github and install it manually.

```bash
python3 setup.py install
```

# support feature

1. Decode Y component of image.
2. Decode 16x16 intra frame.

# examples

1. Test inverse intraprediction, using testCase2()

```Python
python3 prediction.py
```

2. Test CAVLC keyframe decoding, using

```Python
python3 H264Decoder.py
```

# Test data info

Please use H.264 file under /*test*/ folder to test the PyCoder, for the decoding process is not totally supported yet.

Here is some info about test files:

1. lena_x264_baseline_I_16x16.264

    One keyframe of H.264 encoding file.

2. BasketballPass_720p.264

    The H.264 encoding file without B frame.

3. BasketballPass_720p_P_16x16.264

    The H.264 encoding file without B frame, and all P frames are encoding with only P_L0_16x16 mb_type, but may with Intra_4x4 mb_type.

4. BasketballPass_720p_P_16x16_without_Intra_4x4.264

    The H.264 encoding file without B frame, and all P frames are encoding with only P_L0_16x16 mb_type, and without Intra_4x4 mb_type.

# TODO

1. H.264 CABAC decoding process
2. Intra_4x4 decoding process
3. sub_mb_pred decoding process

# Reference
1. The whole code is based on the document of ITU-T Recommendation H.264 05/2003 edition, which I will call *[H.264 standard Book]* in my comment.
2. Most test data is from Richardson's book: *The H.264 Advanced Video Compression Standard, Second Edition*, which I called *[the Richardson Book]* in my comments.