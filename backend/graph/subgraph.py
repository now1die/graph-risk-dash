def get_touched_inode_indices(vfs, transaction):
    """
    Convert transaction inode IDs into
    zero-based graph node indices.
    """

    inodes = vfs.get_all_inodes()

    inode_id_to_index = {
        inode.inode_id: index
        for index, inode in enumerate(inodes)
    }

    touched_indices = []

    for inode_id in transaction.inodes_touched:

        if inode_id in inode_id_to_index:

            touched_indices.append(
                inode_id_to_index[inode_id]
            )

    return touched_indices
