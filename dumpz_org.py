import requests

def binarySearch(n):
    # Known existing page ID
    aux = -1
    lastID = n
    start = 0
    end = n - 1

    # Iterate
    while True:
        # Middle element index
        middle = (start + end) // 2

        if (aux == middle):
            return middle

        print("\t INFO: " + str(middle))

        # Get page
        r = requests.get('https://dumpz.org/'+ str(middle) + '/')

        # See if page doesn't exist
        found = r.text.find("<title>Not Found</title>", 0, 68) == -1
        if found: # Found index is bigger
            start = middle + 1
        else: # Not found index is lower
            end = middle - 1

        aux = middle


if __name__ == '__main__':
    # last Known ID
    f = open("dumpz_org_lastID.txt", "r")
    lastID = int(float(f.read()))
    f.close()

    res = binarySearch(lastID)

    # Number exists - write ID to file
    f = open("dumpz_org_lastID.txt", "w")
    f.write(str(res))
    f.close()

    # Print output
    print("SUCCESS: last ID was "+ str(res))


