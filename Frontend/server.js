import 'dotenv/config';
import express from 'express';
import cookieParser from 'cookie-parser';
import cors from 'cors';
import mongoose from 'mongoose';
import authRoutes from './routes/authRoutes.js';
import { verifyJWT } from './middleware/auth.js';

const app = express();

// Middleware
app.use(express.json());
app.use(cookieParser());
app.use(cors({
  origin: process.env.CLIENT_URL || 'http://localhost:5173',
  credentials: true
}));

// Database connection
try {
  await mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/traffic_system');
  console.log('MongoDB connected');
} catch (error) {
  console.error('MongoDB connection error:', error);
  process.exit(1);
}

// Routes
app.use('/api/auth', authRoutes);

// Protected route example
app.get('/api/dashboard', verifyJWT, (req, res) => {
  res.json({ data: 'Sensitive dashboard data' });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));