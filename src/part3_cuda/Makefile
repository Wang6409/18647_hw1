NVCC ?= nvcc
CXXFLAGS ?= -O2 -std=c++17

TARGET = fft_multiply
SOURCES = main.cu bigint_fft.cu utils.cu

$(TARGET): $(SOURCES)
	$(NVCC) $(CXXFLAGS) -o $@ $(SOURCES) -lcufft

clean:
	rm -f $(TARGET)
