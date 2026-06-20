export const CapsuleWizard = ({ outfits }: any) => {
  return (
    <div style={{ padding: 16 }}>
      <h3>✨ Конструктор образов</h3>
      <p>Сохранено образов: {outfits.length}</p>
    </div>
  );
};
