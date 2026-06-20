import express from 'express';
import cors from 'cors';
import bodyParser from 'body-parser';
import { PrismaClient } from '@prisma/client';
import axios from 'axios';

const app = express();
const prisma = new PrismaClient();
const PORT = process.env.PORT || 3001;
const AI_SERVICE_URL = 'http://localhost:8001';

app.use(cors());
app.use(bodyParser.json());

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'context-aware-captcha-backend' });
});

// Create a new session
app.post('/api/sessions', async (req, res) => {
  const { id } = req.body;
  try {
    const session = await prisma.session.upsert({
      where: { id: id },
      update: {},
      create: { id: id },
    });
    res.json(session);
  } catch (error) {
    res.status(500).json({ error: 'Failed to create session' });
  }
});

// Ingest telemetry data
app.post('/api/interactions', async (req, res) => {
  const { sessionId, type, url, elementId, metadata } = req.body;
  try {
    const interaction = await prisma.interaction.create({
      data: {
        sessionId,
        type,
        url,
        elementId,
        metadata: metadata ? JSON.stringify(metadata) : null,
      },
    });
    res.json(interaction);
  } catch (error) {
    res.status(500).json({ error: 'Failed to log interaction' });
  }
});

// Generate CAPTCHA Challenge
app.post('/api/captcha/generate', async (req, res) => {
  const { sessionId } = req.body;
  
  try {
    const interactions = await prisma.interaction.findMany({
      where: { sessionId },
      orderBy: { timestamp: 'asc' },
      take: 50 // Last 50 interactions
    });

    const aiRes = await axios.post(`${AI_SERVICE_URL}/generate-captcha`, {
      sessionId,
      interactions
    });
    
    const captchaData = aiRes.data;
    
    // Save challenge to DB
    const challenge = await prisma.challenge.create({
      data: {
        sessionId,
        type: captchaData.type,
        difficulty: captchaData.difficulty,
        question: captchaData.question,
        options: JSON.stringify(captchaData.options),
        answer: captchaData.answer
      }
    });

    // Return to client without the answer
    res.json({
      challengeId: challenge.id,
      type: challenge.type,
      difficulty: challenge.difficulty,
      question: challenge.question,
      options: captchaData.options
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Failed to generate CAPTCHA' });
  }
});

// Verify CAPTCHA Challenge
app.post('/api/captcha/verify', async (req, res) => {
  const { challengeId, answer, timeTakenMs } = req.body;
  try {
    const challenge = await prisma.challenge.findUnique({
      where: { id: challengeId }
    });

    if (!challenge) {
      return res.status(404).json({ error: 'Challenge not found' });
    }

    const isCorrect = challenge.answer === answer;

    await prisma.challenge.update({
      where: { id: challengeId },
      data: { 
        isSolved: isCorrect,
        timeTakenMs
      }
    });

    res.json({ success: isCorrect });
  } catch (error) {
    res.status(500).json({ error: 'Failed to verify CAPTCHA' });
  }
});

// Metrics API for Dashboard
app.get('/api/metrics', async (req, res) => {
  try {
    const challenges = await prisma.challenge.findMany();
    const total = challenges.length;
    const solved = challenges.filter(c => c.isSolved).length;
    const failed = total - solved;
    
    const avgTime = challenges.reduce((acc, c) => acc + (c.timeTakenMs || 0), 0) / (total || 1);
    
    res.json({
      total,
      solved,
      failed,
      avgTimeMs: avgTime
    });
  } catch(error) {
    res.status(500).json({ error: 'Failed to fetch metrics' });
  }
});

app.listen(PORT, () => {
  console.log(`Backend server running on http://localhost:${PORT}`);
});
