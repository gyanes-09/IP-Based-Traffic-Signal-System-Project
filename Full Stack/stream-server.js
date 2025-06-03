const Stream = require('node-rtsp-stream');
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Configure your camera streams here
const cameras = [
  {
    name: 'Camera 1',
    rtspUrl: 'rtsp://your-camera-ip:554/stream', // Replace with your camera's RTSP URL
    wsPort: 9998
  },
  // Add more cameras as needed
];

// Create streams for each camera
cameras.forEach(camera => {
  const stream = new Stream({
    name: camera.name,
    streamUrl: camera.rtspUrl,
    wsPort: camera.wsPort,
    ffmpegOptions: {
      '-stats': '',
      '-r': 30,
      '-q:v': 3
    }
  });

  // Handle stream events
  stream.on('start', () => {
    console.log(`Stream started for ${camera.name}`);
  });

  stream.on('error', (err) => {
    console.error(`Stream error for ${camera.name}:`, err);
  });
});

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log('Client connected');

  socket.on('disconnect', () => {
    console.log('Client disconnected');
  });
});

const PORT = 9999;
server.listen(PORT, () => {
  console.log(`Stream server running on port ${PORT}`);
}); 