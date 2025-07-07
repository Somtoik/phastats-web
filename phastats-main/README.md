# Phastats

[![PyPI version](https://badge.fury.io/py/phastats.svg)](https://badge.fury.io/py/phastats)
[![Python versions](https://img.shields.io/pypi/pyversions/phastats.svg)](https://pypi.org/project/phastats/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://somtoik.github.io/phastats/)

**Professional FASTQ Quality Analysis Tool**

Phastats is a comprehensive bioinformatics tool for analyzing FASTQ sequencing data quality. It provides detailed statistics, interactive visualizations, and professional reports to help researchers assess the quality of their sequencing data.

## Features

- **Comprehensive Analysis**: Quality scores, sequence lengths, GC content, and per-base content analysis
- **N50 Calculation**: Genome assembly quality metric not available in FastQC
- **Modern Interface**: Both command-line and web-based interfaces
- **Multiple Output Formats**: HTML, JSON, CSV, and TSV reports
- **High Performance**: Optimized for large file processing with memory-efficient algorithms
- **Professional Reports**: Modern, responsive HTML reports with interactive visualizations

## Quick Start

### Installation

```bash
# Install from PyPI (recommended)
pip install phastats

# Or install from source
git clone https://github.com/somtoik/phastats.git
cd phastats
pip install -e .
```

### Basic Usage

```bash
# Analyze a FASTQ file
phastats input.fastq

# Specify output directory
phastats input.fastq -o output_directory

# Generate specific plots only
phastats input.fastq --plots gc length quality
```

### Python API

```python
from phastats.core import analyze_fastq

# Basic analysis
results = analyze_fastq("input.fastq")

# Advanced analysis with custom parameters
results = analyze_fastq(
    "input.fastq",
    output_dir="my_analysis",
    quality_threshold=25,
    enabled_plots={'gc', 'length', 'quality'}
)
```

## Web Interface

Launch the web interface for easy file upload and analysis:

```bash
cd phastats-web
pip install -r requirements.txt
python app.py
```

Visit `http://localhost:5000` in your browser.

## Requirements

- Python 3.7+
- matplotlib >= 3.3.0
- numpy >= 1.19.0
- pandas >= 1.1.0
- scipy >= 1.5.0

## Running phastats

After installing the necessary packages, `phastats.py` could be run.

Use the following command to update permissions, commonly needed for mac:

```
chmod +x phastats.py
```

Here is how you would run `phastats.py` using this FASTQ file as an argument:

As an example, a sample dataset `data1.fq` is located in the samples folder. To run Phastats on this file, use the following command: 

```
./phastats.py ./samples/data1.fq 
```

### Troubleshooting

If running Phastats returns an error regarding installing packages like pandas, even after using the installation commands, Phastats could be ran using a virtual environment. To make and install this, use the following commands:

```
python3 -m venv myenv
```

```
source myenv/bin/activate
```

```
pip install pandas numpy scipy matplotlib argparse
```

This will create a virtual environment and install the necessary packages in order to run Phastats.

## Implementation

This Python script conducts comprehensive analysis on FASTQ datasets and generates informative plots. Here's a detailed summary of how the code is implemented:

First, Phastats imports its necessary libraries as shown above for functions including parsing, numerical operations and statistical functions, data manipulation, and other operations.

Using a .fq dataset as an argument, Phastats parses command-line arguments to get FASTQ file information such as sequence lengths, quality scores, and GC content; Phastats reads four lines at a time per sequence. 


`getLengthAndQuality` reads a FASTQ file and extracts sequence lengths and quality scores. Quality scores are converted from ASCII characters to Phred scores.

`plot_length_distribution` creates and saves a histogram of sequence lengths to the final html file.

`plot_quality_distribution` creates and saves a histogram of quality scores to the final html file.

`getLengthQualityDistribution` calls `getLengthAndQuality` and the respective plotting functions `plot_length_distribution` and `plot_quality_distribution` to generate the length and quality distribution plots.

`parse_fastq` parses the FASTQ file to extract the total number of sequences and poor quality sequences, total length, GC count, and GC content for each sequence.

`calculate_gc_content` calculates the overall GC content percentage by dividing the GC count by the total length.

`plot_gc_distribution` creates and saves a histogram of GC content per sequence to the final html file.

`getGCDistribution` calls `parse_fastq` and `plot_gc_distribution` to generate the GC content plot.

`getPerBaseSequenceContent` calculates and plots the percentage of each base (A, G, C, T) at each position in each sequence.

`compute_n50` computes the N50 value, a measure of the quality of genome assemblies, by sorting sequence lengths and finding the length at which 50% of the total sequence length is contained.

`print_statistics` outputs various metrics for the provided FASTQ file such as filename, file type encoding, total count of sequences, sequences flagged as poor quality, average sequence length and percentage GC content.


## Benchmarking

The tool's correctness and performance are tested by comparing its output with FastQC(version 0.11.9), a widely-used tool for quality control checks on raw sequence data. 

The datasets for benchmarking include:
- Sequencing data from the Human Genome Structural Variation Consortium, particularly focusing on the Puerto Rican population dataset.
- Public datasets from the NCBI SRA database, specifically samples SRR29246139 and SRR29246140.


### Public Datasets Used

- **SRR29246139.fastq** NPs treated Read 1 (SRR29246139)(Illumina MiSeq) - This sample is a NPs feeded 16S amplicon product from rat gut microbiome were proceeded to sequencing. File contain single end file 1, this sample was submitted by the Capital University of Science and Technology.
 
 **Public Link:** 
 https://www.ncbi.nlm.nih.gov/sra/SRX24764511[accn]


- **SRR29246140.fastq** Control Read 1 (SRR29246140) (Illumina MiSeq) - This sample is a control Sample 16S amplicon product from rat gut microbiome were proceeded to sequencing. File contain single end file 1, this sample was submitted by the Capital University of Science and Technology.

**Public Link:**
https://www.ncbi.nlm.nih.gov/sra/SRX24764510[accn]

### Testing

First, we tested our tool on smaller datasets, such as data1.fq, located at `./samples/data1.fq`. Once we confirmed that our tool ran and returned a correct output on this smaller dataset, we imported the larger datasets using a large dataset extension and ran `Phastats` on these files.

In addition to this, we ran both smaller datasets and larger, real datasets on `FastQC` as well in order to verify correctness of our tool.

## Runtime Comparison

##### For SRR29246139.fastq:

`FastQC`: 12.76 seconds

`Phastats`: 52.2 seconds



## Comparison/Contrast to FastQC

There are various reasons why the outputs of our Phastats tool contrasts from the `FastQC` tool. To start, our Phastats tool computes the N50 of the .fq dataset, while `FastQC` does not. This is useful, for the N50 score provides another measure of the quality of a genome assembly in addition to the information displayed in the resulting html file.
Another reason why these tools differ could be that `FastQC` was coded in Java, while Phastats was created in Python. Because of this, Phastats contains simple, readable syntax, allowing developers to express concepts in fewer lines of code. 
Finally, we have implemented a more modern design for our Phastats HTML file, which may enhance readability compared to `FastQC`.






