import React from 'react';
import styled from 'styled-components';
import './App.css';
import Header from './components/Header';
import AppRouter from './AppRouter';

const MainContainer = styled.div`
    display: flex;
    flex-direction: column;
    text-align: center;
`

const BodyContainer = styled.div`
    display: flex;
    flex-direction: column;
`

function App() {
    return (
        <MainContainer>
            <Header />
            <BodyContainer>
                <AppRouter />
            </BodyContainer>
        </MainContainer>
    );
}

export default App;
