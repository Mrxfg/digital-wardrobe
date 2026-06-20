import { useState } from 'react';

const slides = [
  { title: 'Добро пожаловать', description: 'Организуйте гардероб', icon: '🎯' },
  { title: '📸 Как фотографировать', description: 'Снимайте на белом фоне', icon: '📱' },
  { title: '🧩 Капсулы 8-3', description: '8 вещей = 3 образа', icon: '✨' },
];

export const OnboardingSlider = ({ onComplete }: { onComplete: () => void }) => {
  const [slide, setSlide] = useState(0);

  const next = () => {
    if (slide === slides.length - 1) onComplete();
    else setSlide(slide + 1);
  };

  return (
    <div style={{ padding: 40, textAlign: 'center' }}>
      <div style={{ fontSize: 64 }}>{slides[slide].icon}</div>
      <h2>{slides[slide].title}</h2>
      <p>{slides[slide].description}</p>
      <button onClick={next} style={{ marginTop: 20, padding: 12, background: '#8C7662', color: 'white', border: 'none', borderRadius: 10 }}>
        {slide === slides.length - 1 ? 'Начать' : 'Далее'}
      </button>
    </div>
  );
};
