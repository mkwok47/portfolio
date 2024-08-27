/*
Michael Kwok
CS342 - Final Project
Aug 5, 2024
*/

public class Node {

    private String data;
    private Node link;

    public Node(String data, Node link) {
        this.data = data;
        this.link = link;
    }

    public String getData() {
        return data;
    }

    public Node getNext() {
        return link;
    }

}
