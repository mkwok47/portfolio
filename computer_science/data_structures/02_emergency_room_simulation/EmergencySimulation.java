/*
Michael Kwok
CS342 - Final Project
Aug 5, 2024
*/

import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.io.FileOutputStream;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;
import static java.time.temporal.ChronoUnit.SECONDS;


public class EmergencySimulation  {

    public static void outputToFile (String data, String fileName) {
        PrintWriter outputStream = null;
        try {
            outputStream = new PrintWriter(fileName);
        }
        catch (FileNotFoundException e) {
            System.out.println("Error opening the file" + fileName);
        	System.exit(0);
        }
        outputStream.println(data);
        outputStream.close();
    }

	public static void appendToFile (String data, String fileName) {
		try {
			PrintWriter pw = new PrintWriter(new FileOutputStream(new File(fileName), true));
			pw.append(data);
			pw.close();
		} catch (FileNotFoundException e) {
			System.out.println("Error opening the file" + fileName);
			System.exit(0);
		}
	}
	
	public static void main(String[] args) {

		// ################################################################################################
		// Obtain user input
		// ################################################################################################

		Scanner keyboard = new Scanner(System.in);

		System.out.println("\nWelcome to emergency simulation. Please input number of doctors:");
		int numDoctors = keyboard.nextInt();
		
		System.out.println("Please input time taken per doctor to serve a patient:");
		int doctorTime = keyboard.nextInt();
		
		System.out.println("Please input number of nurses:");
		int numNurses = keyboard.nextInt();
		
		System.out.println("Please input time taken per nurse to serve a patient:");
		int nurseTime = keyboard.nextInt();
		
		System.out.println("Please input number of rooms:");
		int numRooms = keyboard.nextInt();
		
		System.out.println("Please input number of administrative assistants:");
		int numAdminAssist = keyboard.nextInt();
		
		System.out.println("Please input time taken per administrative assistant to serve a patient:");
		int adminAssistTime = keyboard.nextInt();
		
		System.out.println("Please input number of priority queues (at least 3):");
		int numQueues = keyboard.nextInt();
		
		ArrayList<Double> patientArrivProbArr = new ArrayList<Double>();
		for (int i=0; i<numQueues; i++) {
			System.out.println("Please input probability (between 0 and 1) of patient arrival for priority " + i + " (higher priority queue has lower probability):");
			double temp = keyboard.nextDouble();
			patientArrivProbArr.add(temp);
		}
		
		System.out.println("Please input time interval in seconds between events:");
		int timeInterval = keyboard.nextInt();
		
		System.out.println("Please input total time in seconds to run the simulation:");
		int totalTime = keyboard.nextInt();

		keyboard.close();


		// ################################################################################################
		// Create data structures
		// ################################################################################################
		
		// arraylist of priority queues for patients
		ArrayList<Queue> priorityQueues = new ArrayList<Queue>();
		for (int i=1; i<=numQueues; i++) {
			Queue temp = new Queue();
			priorityQueues.add(temp);
		}

		// linked-list stack for doctors
		LinkedStack doctorStack = new LinkedStack();
		ArrayList<Integer> doctorTimers = new ArrayList<Integer>();
		ArrayList<Integer> doctorTimeSpent = new ArrayList<Integer>();
		for (int i=numDoctors; i>0; i--) {
			doctorStack.push("D"+i);
			doctorTimers.add(0);
			doctorTimeSpent.add(0);
		}

		// linked-list stack for nurses
		LinkedStack nurseStack = new LinkedStack();
		ArrayList<Integer> nurseTimers = new ArrayList<Integer>();
		ArrayList<Integer> nurseTimeSpent = new ArrayList<Integer>();
		for (int i=numNurses; i>0; i--) {
			nurseStack.push("N"+i);
			nurseTimers.add(0);
			nurseTimeSpent.add(0);
		}

		// linked-list stack for administrative assistants
		LinkedStack adminAssistStack = new LinkedStack();
		ArrayList<Integer> adminAssistTimers = new ArrayList<Integer>();
		ArrayList<Integer> adminAssistTimeSpent = new ArrayList<Integer>();
		for (int i=numAdminAssist; i>0; i--) {
			adminAssistStack.push("AA"+i);
			adminAssistTimers.add(0);
			adminAssistTimeSpent.add(0);
		}

		// create arraylist of rooms
		ArrayList<String> rooms = new ArrayList<String>();
		ArrayList<Boolean> roomOccupied = new ArrayList<Boolean>();
		for (int i=1; i<=numRooms; i++) {
			rooms.add("Room"+i);
			roomOccupied.add(false);
		}

		// create check-out queue for patients
		Queue checkoutQueue = new Queue();


		// ################################################################################################
		// Run simulation
		// ################################################################################################

		// run simulation for desired totalTime
		int patientNum = 1;
		int patientsServed = 0;
		Map<String, String> nurseRoom = new HashMap<String, String>();
		Map<String, String> doctorRoom = new HashMap<String, String>();
		Map<String, String> roomPatient = new HashMap<String, String>();
		Map<String, String> adminAssistPatient = new HashMap<String, String>();
		ArrayList<String> awaitingDoctor = new ArrayList<String>();
		ArrayList<Integer> waitTimes = new ArrayList<Integer>();
		for (int i=1; i<=numAdminAssist; i++) {
			adminAssistPatient.put("AA"+i, "Available");
		}
		LocalTime endTime = LocalTime.now().plusSeconds(totalTime);
		while (LocalTime.now().until(endTime, SECONDS)>0) {

			// decrement/reset timers, return workers to stack, remove worker from map as needed
			for (int i=0; i<numNurses; i++) {
				int timer = nurseTimers.get(i);
				if (timer >= 1) {
					nurseTimers.set(i, timer-1);
					nurseTimeSpent.set(i, nurseTimeSpent.get(i) + 1);
					// reset if finished
					if (nurseTimers.get(i) <= 0) {
						nurseStack.push("N"+(i+1));
						awaitingDoctor.add(nurseRoom.get("N"+(i+1)));
						nurseRoom.remove("N"+(i+1));
					}
				}
			}
			for (int i=0; i<numDoctors; i++) {
				int timer = doctorTimers.get(i);
				if (timer >= 1) {
					doctorTimers.set(i, timer-1);
					doctorTimeSpent.set(i, doctorTimeSpent.get(i) + 1);
					// reset if finished
					if (doctorTimers.get(i) <= 0) {
						doctorStack.push("D"+(i+1));
						String room = doctorRoom.get("D"+(i+1));
						int roomNum = Integer.parseInt(room.substring(4));
						checkoutQueue.add(roomPatient.get(doctorRoom.get("D"+(i+1))));
						roomPatient.remove(doctorRoom.get("D"+(i+1)));
						doctorRoom.remove("D"+(i+1));
						roomOccupied.set(roomNum-1, false);
					}
				}
			}
			for (int i=0; i<numAdminAssist; i++) {
				int timer = adminAssistTimers.get(i);
				if (timer >= 1) {
					adminAssistTimers.set(i, timer-1);
					adminAssistTimeSpent.set(i, adminAssistTimeSpent.get(i) + 1);
					// reset if finished
					if (adminAssistTimers.get(i) <= 0) {
						adminAssistStack.push("AA"+(i+1));
						adminAssistPatient.put("AA"+(i+1), "Available");
						patientsServed += 1;
					}
				}
			}
			// increment wait times
			for (int i=numQueues-1; i>=0; i--) {
				for (int j=0; j<priorityQueues.get(i).size(); j++) {
					priorityQueues.get(i).incrementWait(j);
				}
			}

			// print status updates
			String outputString = "";
			System.out.println("########################################################");
			// print admin assist
			for (String aa: adminAssistPatient.keySet()) {
				System.out.println(aa + ": " + adminAssistPatient.get(aa));
				outputString += "\n" + aa + ": " + adminAssistPatient.get(aa);
			}
			// print checkout queue
			String checkoutQueuePatients = "";
			for (int i=0; i<checkoutQueue.size(); i++) {
				checkoutQueuePatients += checkoutQueue.getData(i) + " ";
			}
			System.out.println("Checkout Queue: " + checkoutQueuePatients + "\n");
			outputString += "\nCheckout Queue: " + checkoutQueuePatients + "\n";
			// print rooms
			for (String r: roomPatient.keySet()) {
				String tempDoct = null;
				for (String d: doctorRoom.keySet()) {
					if (doctorRoom.get(d).equals(r)) {
						tempDoct = d;
					}
				}
				String tempNurse = null;
				for (String n: nurseRoom.keySet()) {
					if (nurseRoom.get(n).equals(r)) {
						tempNurse = n;
					}
				}
				assert !(tempDoct!=null && tempNurse!=null);
				if (tempDoct!=null) {
					System.out.println(r + ": " + roomPatient.get(r) + " " + tempDoct);
					outputString += "\n" + r + ": " + roomPatient.get(r) + " " + tempDoct;
				} else if (tempNurse!=null) {
					System.out.println(r + ": " + roomPatient.get(r) + " " + tempNurse);
					outputString += "\n" + r + ": " + roomPatient.get(r) + " " + tempNurse;
				} else {
					System.out.println(r + ": " + roomPatient.get(r));
					outputString += "\n" + r + ": " + roomPatient.get(r);
				}
			}
			// print doctors
			System.out.println();
			outputString += "\n";
			for (int i=0; i<numDoctors; i++) {
				if (doctorTimers.get(i)==0) {
					System.out.println("D" + (i+1) + ": Available");
					outputString += "\nD" + (i+1) + ": Available";
				}
			}
			// print nurses
			System.out.println();
			outputString += "\n";
			for (int i=0; i<numNurses; i++) {
				if (nurseTimers.get(i)==0) {
					System.out.println("N" + (i+1) + ": Available");
					outputString += "\nN" + (i+1) + ": Available";
				}
			}
			// print priority queues
			System.out.println();
			outputString += "\n";
			for (int i=0; i<numQueues; i++) {
				String queueContents = ": ";
				for (String j: priorityQueues.get(i).getArray()) {
					queueContents += j+" ";
				}
				System.out.println("Q" + (i+1) + queueContents);
				outputString += "\nQ" + (i+1) + queueContents;
			}
			// overwrite results in simulationOut.txt
			System.out.println();
			outputToFile(outputString, "simulationOut.txt");

			// intake patient and assign priority
			double tempProbability = Math.random();
			for (int i=numQueues-1; i>=0; i--) {
				if (tempProbability < patientArrivProbArr.get(i) || i==0) {
					priorityQueues.get(i).add("P"+patientNum);
					patientNum += 1;
					break;
				};
			}

			// assign nurse to patient and empty room if exists
			if (!nurseStack.isEmpty()) {
				for (int i=0; i<numRooms; i++) {
					if (!roomOccupied.get(i)) {

						// retrieve patient from queue in order of priority
						String patient = null;
						for (int j=numQueues-1; j>=0; j--) {
							if (priorityQueues.get(j).size()>0) {
								waitTimes.add(priorityQueues.get(j).getWait(0));
								patient = priorityQueues.get(j).remove();
								break;
							}
						}
						// skip if no patient
						if (patient == null) {
							break;
						}

						roomOccupied.set(i, true);
						Node nurse = nurseStack.pop();
						roomPatient.put("Room"+(i+1), patient);
						nurseRoom.put(nurse.getData(), "Room"+(i+1));
						nurseTimers.set(Integer.parseInt(nurse.getData().substring(1))-1, nurseTime);
						break;
					}
				}
			}

			// assign doctor to patients in waiting rooms
			ArrayList<String> unmodifiedTemp = new ArrayList<String>();
			for (String r: awaitingDoctor) {
				unmodifiedTemp.add(new String(r));
			}
			for (String r: unmodifiedTemp) {
				Node doctor = doctorStack.pop();
				if (doctor!=null) {
					doctorRoom.put(doctor.getData(), r);
					doctorTimers.set(Integer.parseInt(doctor.getData().substring(1))-1, doctorTime);
					awaitingDoctor.remove(r);
				}
			}

			// assign patients to admin assist as available
			if (checkoutQueue.size() > 0) {
				Node adminAssist = adminAssistStack.pop();
				if (adminAssist!=null) {
					adminAssistPatient.put(adminAssist.getData(), checkoutQueue.remove());
					adminAssistTimers.set(Integer.parseInt(adminAssist.getData().substring(2))-1, adminAssistTime);
				}
			}

			// pause between patients based on timeInterval
			int sleepTime = (int)timeInterval*1000;
			try {
				Thread.sleep(sleepTime);
			} catch (InterruptedException e) {
				Thread.currentThread().interrupt();
				return;
			}
		}

		// ################################################################################################
		// Summary
		// ################################################################################################

		String appendFinalString = "";
		System.out.println("Total patients served: " + patientsServed);
		appendFinalString += "\nTotal patients served: " + patientsServed;
		int waitSum = 0;
		for (int wt: waitTimes) {
			waitSum += wt;
		}
		System.out.println("Average wait time: " + waitSum / waitTimes.size() + " seconds");
		appendFinalString += "\nAverage wait time: " + waitSum / waitTimes.size() + " seconds";
		System.out.println("Total time used: " + totalTime + " seconds");
		appendFinalString += "\nTotal time used: " + totalTime + " seconds";
		System.out.println();
		appendFinalString += "\n";
		for (int i=0; i<adminAssistTimeSpent.size(); i++) {
			System.out.println("AA" + (1+i) + ": " + adminAssistTimeSpent.get(i) + " seconds");
			appendFinalString += "\nAA" + (1+i) + ": " + adminAssistTimeSpent.get(i) + " seconds";
		}
		System.out.println();
		appendFinalString += "\n";
		for (int i=0; i<doctorTimeSpent.size(); i++) {
			System.out.println("D" + (1+i) + ": " + doctorTimeSpent.get(i) + " seconds");
			appendFinalString += "\nD" + (1+i) + ": " + doctorTimeSpent.get(i) + " seconds";
		}
		System.out.println();
		appendFinalString += "\n";
		for (int i=0; i<nurseTimeSpent.size(); i++) {
			System.out.println("N" + (1+i) + ": " + nurseTimeSpent.get(i) + " seconds");
			appendFinalString += "\nN" + (1+i) + ": " + nurseTimeSpent.get(i) + " seconds";
		}
		appendToFile(appendFinalString, "simulationOut.txt");

		System.out.println();

	}
}
