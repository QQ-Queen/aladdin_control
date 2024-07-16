import os
import glob

class FileUtils:
    """
    Contains helper functions for manipulating files. Unlikely that users of the aladdin_auto library will need to use these methods.
    """

    @staticmethod
    def deleteOldestTraces(searchPath: str, maxSize: int):
        """Deletes the oldest trace from the directory until the size of the directory is under the maxSize or there are
        no traces left.

        :param searchPath: path to directory to delete traces from
        :param maxSize: desired maximum size of directory in bytes
        :meta private:
        """
        if not searchPath.endswith("/"):
            searchPath += "/"
        files = list(filter(os.path.isfile, glob.glob(searchPath + "*.zip")))
        files.sort(key=lambda x: os.path.getmtime(x))
        currentSize = FileUtils._getSize(files)
        fileIndex = 0
        while currentSize > maxSize and fileIndex < len(files):
            oldestFile = files[fileIndex]
            fileSize = os.path.getsize(oldestFile)
            os.remove(oldestFile)
            fileIndex+=1
            currentSize -= fileSize

    @staticmethod
    def _getSize(filelist):
        totalSize = 0
        for file in filelist:
            # skip if it is symbolic link
            if not os.path.islink(file):
                try:
                    totalSize += os.path.getsize(file)
                except FileNotFoundError:
                    pass
        return totalSize
