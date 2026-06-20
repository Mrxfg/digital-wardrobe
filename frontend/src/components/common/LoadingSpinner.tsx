export const LoadingSpinner = () => (
  <div style={{
    display: 'inline-block',
    width: 24,
    height: 24,
    border: '3px solid #F4EFE6',
    borderTopColor: '#8C7662',
    borderRadius: '50%',
    animation: 'spin 0.8s linear infinite',
  }}>
    <style>{`
      @keyframes spin {
        to { transform: rotate(360deg); }
      }
    `}</style>
  </div>
);