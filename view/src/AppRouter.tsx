import React from 'react'
import {
    BrowserRouter as Router,
    Switch,
    Route,
    Link
  } from "react-router-dom";
import { LOGIN_ROUTE, USER_SETTINGS_ROUTE, COLLABORATOR_ROUTE } from './Routes';
import Login from './pages/Login';
import UserSettings from './pages/UserSettings';
import CollaboratorRegister from './pages/CollaboratorRegister';

function AppRouter(): JSX.Element {
    return (
        <Router>
            <Switch>
                <Route path={LOGIN_ROUTE}>
                    <Login />
                </Route>
                <Route path={USER_SETTINGS_ROUTE}>
                    <UserSettings />
                </Route>
                <Route path={COLLABORATOR_ROUTE}>
                    <CollaboratorRegister />
                </Route>
            </Switch>
        </Router>
    )
}

export default AppRouter;