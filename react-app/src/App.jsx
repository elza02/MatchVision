import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ChakraProvider, Box } from '@chakra-ui/react';
import Layout from './components/layout/Layout';
import Dashboard from './components/dashboard/Dashboard';
import Teams from './components/teams/Teams';
import Players from './components/players/Players';
import Matches from './components/matches/Matches';
import Analytics from './components/analytics/Analytics';
import StandingsPage from './components/standings/StandingsPage';
import theme from './theme';

function App() {
  return (
    <ChakraProvider theme={theme}>
      <Router>
        <Box minH="100vh" bg="gray.50">
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="/teams/*" element={<Teams />} />
              <Route path="/players/*" element={<Players />} />
              <Route path="/matches/*" element={<Matches />} />
              <Route path="/standings" element={<StandingsPage />} />
              <Route path="/analytics" element={<Analytics />} />
            </Route>
          </Routes>
        </Box>
      </Router>
    </ChakraProvider>
  );
}

export default App;
