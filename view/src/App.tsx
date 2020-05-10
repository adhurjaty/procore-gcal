import React from 'react';
import './App.css';
import Header from './components/Header';
import AppRouter from './AppRouter';

function App() {
    return (
        <div className="App">
            <Header />
            <AppRouter />
        </div>
    );
}

export default App;
