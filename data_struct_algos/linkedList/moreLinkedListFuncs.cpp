#include <cassert>
#include "linkedList.h"
#include "linkedListFuncs.h"



void addIntToEndOfList(LinkedList *list, int value) {
  assert(list!=NULL); // if list is NULL, we can do nothing.

  Node *p; // temporary pointer

  // TODO:
  // (1) Allocate a new node.  p will point to it.
  Node *new_node = new Node;
  p = new_node;

  // (2) Set p's data field to the value passed in
  p->data = value;
  
  // (3) Set p's next field to NULL
  p->next = NULL;

  if (list->head == NULL) {

    // (4) Make both head and tail of this list point to p
    list->head = p;
    list->tail = p;
    
  } else {

    // Add p at the end of the list.

    // (5) The current node at the tail? Make it point to p instead of NULL
    list->tail->next = p;

    // (6) Make the tail of the list be p now.
    list->tail = p;

  }

}

void addIntToStartOfList(LinkedList *list, int value) {
  assert(list!=NULL); // if list is NULL, we can do nothing.

  // Add code for this.  
  // HINTS:
  //  You will need to allocate a new Node.
  //  You will need two cases just as in addIntToEndOfList,
  //  one for when list->head is NULL and another for when it is not.
  // You need to consider how to make sure that list->head changes to point to the new node
  // that you allocated.  And you will need to make sure that when you are done, 
  // that if the new node is now the ONLY thing on the list, that tail points to it also,
  // and that the new node is pointing to NULL.
  // Otherwise, you'll need to be sure that 
  //   if it is the only node on the list, or to the "old" head if there

  Node *p; // temporary pointer

  // TODO:
  // (1) Allocate a new node.  p will point to it.
  Node *new_node = new Node;
  p = new_node;

  // (2) Set p's data field to the value passed in
  p->data = value;

  if (list->head == NULL) {

    // (3) Make both head and tail of this list point to p
    p->next = NULL;
    list->head = p;
    list->tail = p;
    
  } else {

    // Add p at the beginning of the list.

    // (4) Set p's next field to the current head pointer    
    p->next = list->head;

    // (5) Make the head of the list be p now.
    list->head = p;

  }

}

// list: ptr to a linked list of Node (each with int data, and Node * next)
// Return a pointer to node with the largest value.
// You may assume list has at least one element  
// If more than one element has largest value, 
//  break tie by returning a pointer to the one the occurs
//  earlier in the list, i.e. closer to the head

Node * pointerToMax(LinkedList *list) {

  // Code may assume that these assertions are true;
  //  so does not need to do error checking for these conditions.
  assert(list!=NULL);
  assert(list->head != NULL);

  // TODO: Insert code here to calculate and return
  //   value of pointer to max element (first one if ties.)

  Node *value = list->head;

  for (Node *n = list->head; n != nullptr; n = n->next) { // non-numerical for-loop
    if (n->data > value->data) {
      value = n;
    }
  }

  return value;

}

// list: ptr to a linked list of Node (each with int data, and Node * next)
// Return a pointer to node with the smallest value.  
// You may assume list has at least one element
// If more than one element has smallest value, 
//  break tie by returning a pointer to the one the occurs
//  earlier in the list, i.e. closer to the head


Node * pointerToMin(LinkedList *list) {

  // Code may assume that these assertions are true;
  //  so does not need to do error checking for these conditions.

  assert(list!=NULL);
  assert(list->head != NULL);

  // TODO: Insert code here to calculate and return
  //   value of pointer to min element 
  //   (first one such value that occurs if there are ties.)

  Node *value = list->head;

  for (Node *n = list->head; n != nullptr; n = n->next) { // non-numerical for-loop
    if (n->data < value->data) {
      value = n;
    }
  }

  return value;

}

// list: ptr to a linked list of Node (each with int data, and Node * next)
// Return the largest value in the list.
// This value may be unique, or may occur more than once
// You may assume list has at least one element

int largestValue(LinkedList *list) {

  // Code may assume that these assertions are true;
  //  so does not need to do error checking for these conditions.

  assert(list!=NULL);
  assert(list->head != NULL);

  // TODO: Insert code here to calculate and return
  //   largest value in list (which may not be unique).

  int value = list->head->data;

  for (Node *n = list->head; n != nullptr; n = n->next) { // non-numerical for-loop
    if (n->data > value) {
      value = n->data;
    }
  }

  return value;

}

// list: ptr to a linked list of Node (each with int data, and Node * next)
// Return the smallest value in the list.
// This value may be unique, or may occur more than once
// You may assume list has at least one element

int smallestValue(LinkedList *list) {
  // Code may assume that these assertions are true;
  //  so does not need to do error checking for these conditions.

  assert(list!=NULL);
  assert(list->head != NULL);

  // TODO: Insert code here to calculate and return
  //   smallest value in list (which may not be unique).

  int value = list->head->data;

  for (Node *n = list->head; n != nullptr; n = n->next) { // non-numerical for-loop
    if (n->data < value) {
      value = n->data;
    }
  }

  return value;

}

// list: ptr to a linked list of Node (each with int data, and Node * next)
// Return the sum of all values in the list.
// You may assume that list is not NULL
// However, the list may be empty (i.e. list->head may be NULL)
//  in which case your code should return 0.

int sum(LinkedList * list) {
  // Code may assume that these assertions are true;
  //  so does not need to do error checking for these conditions.

  assert(list!=NULL);

  // TODO: Insert code here to calculate and return
  //   sum of all values in list (0 if there are none).

  int sum = 0;

  for (Node *n = list->head; n != nullptr; n = n->next) { // non-numerical for-loop
    sum += n->data;
  }

  return sum;

}

