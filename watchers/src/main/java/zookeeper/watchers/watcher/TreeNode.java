package zookeeper.watchers.watcher;

import java.util.List;

public class TreeNode {

    private final String         path;
    private final String         data;
    private final List<TreeNode> children;

    public TreeNode(String path, String data, List<TreeNode> children) {
        this.path     = path;
        this.data     = data;
        this.children = children != null ? List.copyOf(children) : List.of();
    }

    public String getPath() {
        return path;
    }

    public String getData() {
        return data;
    }

    public List<TreeNode> getChildren() {
        return children;
    }

    public String getName() {
        int idx = path.lastIndexOf('/');
        return idx >= 0 ? path.substring(idx + 1) : path;
    }

    @Override
    public String toString() {
        return getName();
    }
}
