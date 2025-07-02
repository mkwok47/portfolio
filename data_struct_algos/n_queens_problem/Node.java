/*
Michael Kwok
CS342 - Assignment 3
Jul 22, 2024
*/

public class Node {

    private int row;
    private int col;
    private Node link;

    public Node(int row, int col, Node link) {
        this.row = row;
        this.col = col;
        this.link = link;
    }

    public static boolean conflictExists(Node head, int row, int col, int n) {
        for (Node cursor=head; cursor!=null; cursor=cursor.link) {

            // check vertical and horizontal
            if (row==cursor.row || col==cursor.col) {
                return true;
            }

            // check diagonal going up and left
            int r = cursor.row-1;
            int c = cursor.col-1;
            while (r>=0 && c>=0) {
                if (row==r && col==c) {
                    return true;
                }
                r--;
                c--;
            }
            
            // check diagonal going down and right
            int r2 = cursor.row+1;
            int c2 = cursor.col+1;
            while (r2<n && c2<n) {
                if (row==r2 && col==c2) {
                    return true;
                }
                r2++;
                c2++;
            }

            // check diagonal going up and right
            int r3 = cursor.row-1;
            int c3 = cursor.col+1;
            while (r3>=0 && c3<n) {
                if (row==r3 && col==c3) {
                    return true;
                }
                r3--;
                c3++;
            }

            // check diagonal going down and left
            int r4 = cursor.row+1;
            int c4 = cursor.col-1;
            while (r4<n && c4>=0) {
                if (row==r4 && col==c4) {
                    return true;
                }
                r4++;
                c4--;
            }

        }
        return false;
    }

    public static void printQueens(Node head) {
        int counter = 1;
        for (Node cursor=head; cursor!=null; cursor=cursor.link) {
            System.out.println("Queen " + counter + ": (" + cursor.row + ", " + cursor.col + ")");
            counter++;
        }
    }
}
