from vfs.filesystem import VirtualFileSystem


vfs = VirtualFileSystem()

vfs.create("/home", "directory")
vfs.create("/home/test.txt", "file")

vfs.link(
    "/home/test.txt",
    "/home/test_link.txt"
)

print("BEFORE UNLINK")
print(vfs.get_all_inodes())

vfs.unlink("/home/test.txt")

print("AFTER UNLINK")
print(vfs.get_all_inodes())

print("REMAINING FILE")
print(vfs.get_inode("/home/test_link.txt"))
