import React from 'react';
import styled from 'styled-components';
import './App.css';
import Header from './components/Header';
import AppRouter from './AppRouter';

const BodyContainer = styled.div`
    display: flex;
    flex-direction: column;
`

function App() {
    return (
        <div className="App">
            <Header />
            <BodyContainer>
                <AppRouter />
            </BodyContainer>
        </div>
    );
}

export default App;
