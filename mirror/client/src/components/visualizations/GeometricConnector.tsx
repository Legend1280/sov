/**
 * GeometricConnector - Two squares connected by a triangle with live Pulse coherence
 * 
 * A semantic geometric visualization showing two squares (Mirror and Core) with a triangle
 * displaying the real-time coherence score from PulseBridge communication.
 * 
 * Author: Brady Simmons
 * Copyright: © 2025 Sovereignty Foundation. All rights reserved.
 */

import { useEffect, useRef, useState } from 'react';
import { usePulse } from '@/core/pulse/usePulse';

export function GeometricConnector() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [coherence, setCoherence] = useState(0);
  const [pulseCount, setPulseCount] = useState(0);
  const { onPulse } = usePulse('mirror↔core');

  // Subscribe to Pulse events
  useEffect(() => {
    const unsubscribe = onPulse((pulse) => {
      setCoherence(pulse.coherence);
      setPulseCount(prev => prev + 1);
    });

    return unsubscribe;
  }, [onPulse]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const resizeCanvas = () => {
      const container = canvas.parentElement;
      if (!container) return;
      
      canvas.width = container.clientWidth;
      canvas.height = container.clientHeight;
      draw();
    };

    const draw = () => {
      const width = canvas.width;
      const height = canvas.height;

      // Clear canvas
      ctx.clearRect(0, 0, width, height);

      // Calculate positions
      const squareSize = 120;
      const leftSquareX = width * 0.25 - squareSize / 2;
      const rightSquareX = width * 0.75 - squareSize / 2;
      const squareY = height / 2 - squareSize / 2;

      // Draw left square (Mirror)
      const mirrorGradient = ctx.createLinearGradient(
        leftSquareX, squareY, 
        leftSquareX + squareSize, squareY + squareSize
      );
      mirrorGradient.addColorStop(0, '#3b82f6');
      mirrorGradient.addColorStop(1, '#1e40af');
      
      ctx.fillStyle = mirrorGradient;
      ctx.fillRect(leftSquareX, squareY, squareSize, squareSize);
      ctx.strokeStyle = '#1e40af';
      ctx.lineWidth = 3;
      ctx.strokeRect(leftSquareX, squareY, squareSize, squareSize);

      // Add glow effect to Mirror square
      ctx.shadowColor = '#3b82f6';
      ctx.shadowBlur = 20;
      ctx.strokeRect(leftSquareX, squareY, squareSize, squareSize);
      ctx.shadowBlur = 0;

      // Draw right square (Core)
      const coreGradient = ctx.createLinearGradient(
        rightSquareX, squareY,
        rightSquareX + squareSize, squareY + squareSize
      );
      coreGradient.addColorStop(0, '#8b5cf6');
      coreGradient.addColorStop(1, '#5b21b6');
      
      ctx.fillStyle = coreGradient;
      ctx.fillRect(rightSquareX, squareY, squareSize, squareSize);
      ctx.strokeStyle = '#5b21b6';
      ctx.lineWidth = 3;
      ctx.strokeRect(rightSquareX, squareY, squareSize, squareSize);

      // Add glow effect to Core square
      ctx.shadowColor = '#8b5cf6';
      ctx.shadowBlur = 20;
      ctx.strokeRect(rightSquareX, squareY, squareSize, squareSize);
      ctx.shadowBlur = 0;

      // Calculate triangle points (connecting the squares)
      const leftSquareCenter = {
        x: leftSquareX + squareSize,
        y: squareY + squareSize / 2
      };
      const rightSquareCenter = {
        x: rightSquareX,
        y: squareY + squareSize / 2
      };
      const triangleTop = {
        x: width / 2,
        y: height / 2 - 100
      };

      // Draw triangle with coherence-based color
      const triangleColor = getCoherenceColor(coherence);
      const triangleGradient = ctx.createLinearGradient(
        width / 2, triangleTop.y,
        width / 2, squareY + squareSize / 2
      );
      triangleGradient.addColorStop(0, triangleColor.light);
      triangleGradient.addColorStop(1, triangleColor.dark);

      ctx.beginPath();
      ctx.moveTo(leftSquareCenter.x, leftSquareCenter.y);
      ctx.lineTo(triangleTop.x, triangleTop.y);
      ctx.lineTo(rightSquareCenter.x, rightSquareCenter.y);
      ctx.closePath();
      
      ctx.fillStyle = triangleGradient;
      ctx.fill();
      ctx.strokeStyle = triangleColor.dark;
      ctx.lineWidth = 3;
      ctx.stroke();

      // Add glow effect to triangle based on coherence
      ctx.shadowColor = triangleColor.light;
      ctx.shadowBlur = coherence * 30;
      ctx.stroke();
      ctx.shadowBlur = 0;

      // Draw coherence score in the triangle center
      const triangleCenter = {
        x: width / 2,
        y: (triangleTop.y + squareY + squareSize / 2) / 2
      };

      // Draw coherence percentage
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 32px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(`${Math.round(coherence * 100)}%`, triangleCenter.x, triangleCenter.y - 10);

      // Draw "Coherence" label
      ctx.font = '14px sans-serif';
      ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
      ctx.fillText('Coherence', triangleCenter.x, triangleCenter.y + 15);

      // Add labels to squares
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 18px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      
      ctx.fillText('Mirror', leftSquareX + squareSize / 2, squareY + squareSize / 2 - 10);
      ctx.font = '12px sans-serif';
      ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
      ctx.fillText('UI Layer', leftSquareX + squareSize / 2, squareY + squareSize / 2 + 10);

      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 18px sans-serif';
      ctx.fillText('Core', rightSquareX + squareSize / 2, squareY + squareSize / 2 - 10);
      ctx.font = '12px sans-serif';
      ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
      ctx.fillText('Reasoner', rightSquareX + squareSize / 2, squareY + squareSize / 2 + 10);

      // Draw pulse count at the bottom
      ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
      ctx.font = '14px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(`Pulses: ${pulseCount}`, width / 2, height - 30);
    };

    const getCoherenceColor = (coherence: number) => {
      if (coherence >= 0.9) {
        return { light: '#10b981', dark: '#059669' }; // Green (high coherence)
      } else if (coherence >= 0.7) {
        return { light: '#f59e0b', dark: '#d97706' }; // Amber (medium coherence)
      } else {
        return { light: '#ef4444', dark: '#dc2626' }; // Red (low coherence)
      }
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    return () => {
      window.removeEventListener('resize', resizeCanvas);
    };
  }, [coherence, pulseCount]);

  return (
    <div className="w-full h-full flex flex-col bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="flex-1 flex items-center justify-center">
        <canvas
          ref={canvasRef}
          className="w-full h-full"
        />
      </div>
      
      {/* Stats panel */}
      <div className="px-6 py-4 bg-slate-900/50 border-t border-slate-700 flex items-center justify-between">
        <div className="text-sm text-slate-400">
          <span className="font-semibold text-slate-300">Geometric Pulse Connector</span>
          <span className="mx-2">•</span>
          <span>Live semantic communication</span>
        </div>
        <div className="flex gap-6 text-sm">
          <div>
            <span className="text-slate-400">Coherence: </span>
            <span className={`font-bold ${
              coherence >= 0.9 ? 'text-green-400' :
              coherence >= 0.7 ? 'text-amber-400' :
              'text-red-400'
            }`}>
              {Math.round(coherence * 100)}%
            </span>
          </div>
          <div>
            <span className="text-slate-400">Pulses: </span>
            <span className="font-bold text-blue-400">{pulseCount}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
