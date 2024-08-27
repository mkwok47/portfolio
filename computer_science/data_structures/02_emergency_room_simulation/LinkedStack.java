/*
Michael Kwok
CS342 - Final Project
Aug 5, 2024
*/

public class LinkedStack {
    private Node top = null;
    private int numItems = 0;

    public void push(String data) {
        top = new Node(data, top);
        numItems += 1;
    }

    public Node pop() {
        if (top == null) {
            // System.out.println("Nobody is available");
            return null;
        }
        Node answer = top;
        top = answer.getNext();
        numItems -= 1;
        return answer;
    }

    public boolean isEmpty() {
        return numItems==0;
    }

}
