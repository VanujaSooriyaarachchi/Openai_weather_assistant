const io = require('socket.io-client');

// Connect to the WebSocket server (Socket.IO)
const socket = io('http://localhost:5000', {
  transports: ['websocket'],
});

socket.on('connect', () => {
  console.log('Connected to the WebSocket server');
  // Send a test message
  socket.emit('message', "Hello, I want to know the weather in New York");
});

socket.on('message', (data) => {
  console.log('Received message:', data);
  // Add additional logic to handle different types of messages
});

socket.on('disconnect', () => {
  console.log('Disconnected from WebSocket server');
});

socket.on('error', (error) => {
  console.error('Error:', error);
});
