/*
Michael Kwok
CS342 - Assignment 3
Jul 22, 2024
*/

import java.util.ArrayList;
import java.util.List;

public class MainProgram {
	public static void main(String[] args) {
		nQueen(10);
	}

	public static ArrayList<List<Integer>> getPermutations(List<Integer> arr) {
		ArrayList<List<Integer>> permutationList = new ArrayList<>();
		if (arr.size() == 1) {
			permutationList.add(arr);
			return permutationList;
		} else {
			for (int i = 0; i < arr.size(); i++) {
				Integer currentElement = arr.get(i);
				List<Integer> remainingElements = new ArrayList<>(arr); // Copy the original list
				remainingElements.remove(i); // Remove the current element from the copy
	
				ArrayList<List<Integer>> remainingPermutations = getPermutations(remainingElements);
				for (List<Integer> remainingPermutation : remainingPermutations) {
					remainingPermutation.add(0, currentElement); // Prepend current element
					permutationList.add(remainingPermutation);
				}
			}
			return permutationList;
		}
	}

	public static void nQueen(int n) {

		assert n >= 1;

		// build permutations
		List<Integer> rowNums = new ArrayList<Integer>();
		for (int i=0; i<n; i++) {
			rowNums.add(i);
		}
		ArrayList<List<Integer>> colPositionArr = getPermutations(rowNums);

		boolean ultimateSuccess = false;
		for (int i=0; i<colPositionArr.size(); i++) {
			
			boolean success = true;
			List<Integer> permutation = colPositionArr.get(i);

			// establish first queen (node)
			int queen1Col = permutation.get(0);
			Node head = new Node(0, queen1Col, null);

			// push next queen's position to stack if no conflict
			int row = 1;
			while (row < n) {
				int col = permutation.get(row);
				if (!Node.conflictExists(head, row, col, n)) {
					head = new Node(row, col, head);
					row++;
				} else {
					success = false;
					break;
				}
			}

			if (success) {
				Node.printQueens(head);
				ultimateSuccess = true;
				break;
			} 
		}

		// no solution if still no success after trying all permutations
		if (!ultimateSuccess) {
			System.out.println("No solution");
		}
	}
}
