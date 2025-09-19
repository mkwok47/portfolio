/*
Michael Kwok
CS342 - Final Project
Aug 5, 2024
*/

import java.util.ArrayList;
import java.util.Comparator;

public class Queue {

    private ArrayList<String> queue = new ArrayList<String>();
    private ArrayList<Integer> waitTimes = new ArrayList<Integer>();
    private int front = 0;
    private int rear = 0;

    public Queue clone() {
        Queue newQueue = new Queue();
        for (String s: this.queue) {
            newQueue.add(s);
        }
        return newQueue;
    }     

    public void add(String element) {
        queue.add(element);
        rear += 1;
        waitTimes.add(0);
    }

    public String remove() {
        String returnElement = queue.get(front);
        queue.remove(front);
        rear -= 1;
        return returnElement;
    }

    public int size() {
        assert queue.size() == rear - front;
        return queue.size();
    }

    public void incrementWait(int i) {
        waitTimes.set(i, waitTimes.get(i)+1);
    }

    public void sort() {
        queue.sort(Comparator.naturalOrder());
    }

    public String getData(int i) {
        return queue.get(i);
    }

    public ArrayList<String> getArray() {
        return queue;
    }

    public int getWait(int i) {
        return waitTimes.get(i);
    }

}
