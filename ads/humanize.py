# Make file sizes readable for human beings
def natural_size(count: int) -> str:
    """Using the given integer file size, it returns a string that represents that file size as "___ [KB/MB/GB]", making it easier for the user to read

    Args:
        count (int): The file size as an integer

    Returns:
        str: The file size as a readable string
    """
    fcount = float(count)
    k = 1024
    m = k * k
    g = m * k
    if fcount < k:
        return str(count) + "B"
    if fcount >= k and fcount < m:
        return str(int(fcount / (k / 10.0)) / 10.0) + "KB"
    if fcount >= m and fcount < g:
        return str(int(fcount / (m / 10.0)) / 10.0) + "MB"
    return str(int(fcount / (g / 10.0)) / 10.0) + "GB"