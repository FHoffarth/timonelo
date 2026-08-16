import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
}
interface State {
  hasError: boolean;
}

/**
 * App-wide error boundary. Any render error is caught here and shown as a calm,
 * recoverable message instead of a blank white screen. Release-critical: the
 * app must never unmount to nothing when a single view throws.
 */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // Surface for diagnostics without crashing the tree.
    console.error('Timonelo caught a render error:', error, info.componentStack);
  }

  private reset = () => {
    this.setState({ hasError: false });
    window.location.assign('/');
  };

  render() {
    if (!this.state.hasError) return this.props.children;
    return (
      <div
        role="alert"
        style={{
          minHeight: '100vh',
          display: 'grid',
          placeItems: 'center',
          background: '#f4f2ed',
          color: '#0c1b2a',
          fontFamily: 'Inter, system-ui, sans-serif',
          padding: '2rem',
        }}
      >
        <div style={{ maxWidth: '30rem', textAlign: 'center' }}>
          <p style={{ fontSize: '0.7rem', letterSpacing: '0.2em', textTransform: 'uppercase', color: '#5b6570' }}>
            Timonelo
          </p>
          <h1 style={{ fontFamily: 'Newsreader, Georgia, serif', fontSize: '1.75rem', margin: '0.75rem 0' }}>
            This view could not be opened.
          </h1>
          <p style={{ color: '#5b6570', fontSize: '0.95rem', lineHeight: 1.6 }}>
            Something went wrong loading this page. Your orientation data is safe — please return to the
            start and try again.
          </p>
          <button
            onClick={this.reset}
            style={{
              marginTop: '1.5rem',
              background: '#0c1b2a',
              color: '#fff',
              border: 'none',
              padding: '0.75rem 1.5rem',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: 'pointer',
              borderRadius: '2px',
            }}
          >
            Return to start
          </button>
        </div>
      </div>
    );
  }
}
