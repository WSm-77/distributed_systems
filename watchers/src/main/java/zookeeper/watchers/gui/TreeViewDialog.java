package zookeeper.watchers.gui;

import zookeeper.watchers.watcher.TreeNode;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.DefaultTreeCellRenderer;
import javax.swing.tree.DefaultTreeModel;
import java.awt.*;

/**
 * Modal dialog that displays the full subtree of /a using a JTree.
 *
 * Each node shows its name and, if non-empty, its data value in parentheses.
 */
public class TreeViewDialog {

    private static final Color COLOR_BG      = new Color(30, 32, 40);
    private static final Color COLOR_TREE_BG = new Color(22, 24, 30);
    private static final Color COLOR_TEXT    = new Color(220, 223, 228);
    private static final Color COLOR_ACCENT  = new Color(97, 175, 239);
    private static final Color COLOR_GREEN   = new Color(152, 195, 121);
    private static final Color COLOR_MUTED   = new Color(130, 137, 151);

    /** Show the dialog (must be called on the EDT). */
    public static void show(TreeNode root) {
        JDialog dialog = new JDialog((Frame) null, "ZooKeeper Tree – /a", true);
        dialog.setSize(520, 500);
        dialog.setLocationRelativeTo(null);
        dialog.getContentPane().setBackground(COLOR_BG);
        dialog.setLayout(new BorderLayout(0, 0));

        // ── Header ────────────────────────────────────────────────────────
        JLabel header = new JLabel("  🌲  Subtree of  /a", SwingConstants.LEFT);
        header.setFont(new Font("Segoe UI", Font.BOLD, 15));
        header.setForeground(COLOR_ACCENT);
        header.setOpaque(true);
        header.setBackground(new Color(20, 22, 30));
        header.setBorder(new EmptyBorder(14, 18, 14, 18));
        dialog.add(header, BorderLayout.NORTH);

        // ── Tree ──────────────────────────────────────────────────────────
        DefaultMutableTreeNode treeRoot = buildSwingNode(root);
        JTree tree = new JTree(new DefaultTreeModel(treeRoot));
        tree.setBackground(COLOR_TREE_BG);
        tree.setForeground(COLOR_TEXT);
        tree.setFont(new Font("JetBrains Mono", Font.PLAIN, 13));
        tree.setBorder(new EmptyBorder(8, 8, 8, 8));
        tree.setRowHeight(24);
        // Expand all nodes
        expandAll(tree);

        // Custom cell renderer
        tree.setCellRenderer(new DefaultTreeCellRenderer() {
            @Override
            public Component getTreeCellRendererComponent(
                    JTree t, Object value, boolean sel, boolean expanded,
                    boolean leaf, int row, boolean hasFocus) {
                super.getTreeCellRendererComponent(t, value, sel, expanded, leaf, row, hasFocus);
                setBackgroundNonSelectionColor(COLOR_TREE_BG);
                setBackgroundSelectionColor(new Color(50, 55, 70));
                setForeground(sel ? COLOR_ACCENT : COLOR_TEXT);
                setBorderSelectionColor(COLOR_ACCENT);
                setLeafIcon(null);
                setOpenIcon(null);
                setClosedIcon(null);
                return this;
            }
        });

        JScrollPane scroll = new JScrollPane(tree);
        scroll.setBorder(BorderFactory.createLineBorder(new Color(55, 58, 70), 1));
        scroll.getViewport().setBackground(COLOR_TREE_BG);

        JPanel center = new JPanel(new BorderLayout());
        center.setBackground(COLOR_BG);
        center.setBorder(new EmptyBorder(12, 16, 12, 16));
        center.add(scroll, BorderLayout.CENTER);

        // ── Legend ────────────────────────────────────────────────────────
        JLabel legend = new JLabel("  Node name  (data value if present)");
        legend.setFont(new Font("Segoe UI", Font.ITALIC, 11));
        legend.setForeground(COLOR_MUTED);
        legend.setBorder(new EmptyBorder(0, 0, 6, 0));
        center.add(legend, BorderLayout.SOUTH);

        dialog.add(center, BorderLayout.CENTER);

        // ── Close button ──────────────────────────────────────────────────
        JButton close = new JButton("Close");
        close.setFont(new Font("Segoe UI", Font.BOLD, 12));
        close.setForeground(Color.WHITE);
        close.setBackground(new Color(50, 55, 70));
        close.setFocusPainted(false);
        close.setBorder(new EmptyBorder(8, 20, 8, 20));
        close.addActionListener(e -> dialog.dispose());

        JPanel footer = new JPanel(new FlowLayout(FlowLayout.RIGHT, 16, 10));
        footer.setBackground(new Color(20, 22, 30));
        footer.add(close);
        dialog.add(footer, BorderLayout.SOUTH);

        dialog.setVisible(true);
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    private static DefaultMutableTreeNode buildSwingNode(TreeNode node) {
        String label = node.getName();
        if (node.getData() != null && !node.getData().isBlank()) {
            label += "  (" + node.getData() + ")";
        }
        DefaultMutableTreeNode swingNode = new DefaultMutableTreeNode(label);
        for (TreeNode child : node.getChildren()) {
            swingNode.add(buildSwingNode(child));
        }
        return swingNode;
    }

    private static void expandAll(JTree tree) {
        for (int i = 0; i < tree.getRowCount(); i++) {
            tree.expandRow(i);
        }
    }
}
