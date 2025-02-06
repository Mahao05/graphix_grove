const socket = io();

// Generic socket listener for future use
socket.on("updateData", (data) => {
  console.log("Real-time data:", data);
});
