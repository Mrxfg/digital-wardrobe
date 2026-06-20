export const WearCalendar = ({  history }: any) => {
  return (
    <div style={{ padding: 16 }}>
      <h3>Календарь носки</h3>
      <p>Отметок: {history.length}</p>
    </div>
  );
};
