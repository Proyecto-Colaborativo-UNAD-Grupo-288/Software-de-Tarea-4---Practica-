![Banner](https://raw.githubusercontent.com/Proyecto-Colaborativo-UNAD-Grupo-288/Software-de-Tarea-4---Practica-/refs/heads/main/images.jpg)

# Software-de-Tarea-4---Practica-
Espacio de trabajo destinado para el desarrollo de la tarea 4, practicas simuladas  
#
import { useEffect, useRef } from 'react';
import { asciify } from 'asciify-engine';

export function AsciiImage({ src }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (canvasRef.current) {
      asciify(src, canvasRef.current, { options: {
  fontSize: 5,
  charSpacing: 0.7,
  brightness: 0.7,
  contrast: 0.65,
  colorMode: 'matrix',
  accentColor: '#c850ff',
  animationStyle: 'glitch',
  animationSpeed: 0.5,
  dotSizeRatio: 1,
  ditherStrength: 0.2,
  hoverStrength: 0.7,
  hoverRadius: 0.18,
  hoverEffect: 'attract',
  hoverColor: '#a5d6ff',
  artStyle: 'particles',
  chromaKey: 'blue-screen'
      } });
    }
  }, [src]);

  return <canvas ref={canvasRef} style={{ display: 'block', width: '100%', height: 'auto' }} />;
}
