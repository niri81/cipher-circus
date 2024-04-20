import argparse
import matplotlib.pyplot as plt


def readFile(filename: str, stride: int) -> dict[int, list[int]]:
    """
    Read input file and return a list of byte values
    :param stride: Stride of histogram bins
    :param str filename: Name of the file to read
    :return: List of byte values in the given file
    """
    byte_list = []
    output = {}
    with open(filename, 'rb') as f:
        while read_byte := f.read(1):
            byte_list.append(int.from_bytes(read_byte, byteorder='little'))
    if stride:
        for i in range(stride):
            output[i] = byte_list[i::stride]
    else:
        output[0] = byte_list
    return output


def createPercentagePlot(byte_list: dict[int, float], out_filename: str, stride: int) -> None:
    """
    Create a histogram of byte values
    :param stride: Given bin
    :param str out_filename: Name of the output file
    :param dict[int, float] byte_list: Dictionary of byte values with relative properties
    """
    fig, ax = plt.subplots()
    ax.bar(list(byte_list.keys()), list(byte_list.values()), width=1)
    ax.set_xlabel('Byte values')
    ax.set_ylabel('Relative distribution')
    ax.set_title(f'Relative distribution of byte values (bin {stride})')
    fig.savefig(out_filename)


def createAbsolutePlot(data: list[int], out_filename: str, stride: int) -> None:
    """
    Create plot from given array with byte values with absolute values, that is shown and saved
    :param stride: Given bin
    :param str out_filename: Name of the output file
    :param list[int] data: Array with byte values
    """
    fig, ax = plt.subplots()
    ax.hist(data, bins=range(256))
    ax.set_xlabel('Byte values')
    ax.set_ylabel('Absolute distribution')
    ax.set_title(f'Absolute distribution of byte values (bin {stride})')
    fig.savefig(out_filename)


def createStatisticalDistribution(data: list[int], percentage: bool) -> dict[int, float]:
    """
    Create statistical distribution from given array with byte values and print it out
    :param list[int] data: Provided data as a list of integer values
    :param bool percentage: Calculates percentage distribution
    :return: Dictionary of statistical distribution
    """
    distribution = {}
    for d in data:
        if distribution.get(d):
            distribution[d] += 1
        else:
            distribution[d] = 1
    if percentage:
        for key in distribution.keys():
            distribution[key] /= len(data)
    sorted_dict = {key: distribution[key] if distribution.get(key) else 0 for key in range(256)}
    return sorted_dict


def main():
    """
    Main function parsing the command line arguments, reading the provided file and creating the histogram plot
    """
    parser = argparse.ArgumentParser(description='Create histogram from given byte values')
    parser.add_argument('-p', '--percentage',
                        help='Give percentages in statistical distribution (absolute values if not provided)',
                        action='store_true')
    parser.add_argument('-s', '--stride', help='Stride of histogram plot', type=int, default=1)
    parser.add_argument('filename', help='Name of the file to read')
    parser.add_argument('out_filename', help='Name of the output file')

    args = parser.parse_args()
    data = readFile(args.filename, args.stride)
    for i in range(args.stride):
        if args.percentage:
            percentage_data = createStatisticalDistribution(data[i], args.percentage)
            createPercentagePlot(percentage_data, args.out_filename + str(i) + '.png', i)
        else:
            createAbsolutePlot(data[i], args.out_filename + str(i) + '.png', i)


if __name__ == '__main__':
    main()
