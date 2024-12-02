import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ChakraProvider, Box, CSSReset } from '@chakra-ui/react';
import Navbar from './components/layout/Navbar';
import Sidebar from './components/layout/Sidebar';
import Dashboard from './components/dashboard/Dashboard';
import Competitions from './components/competitions/Competitions';
import Teams from './components/teams/Teams';
import Matches from './components/matches/Matches';
import Players from './components/players/Players';
import Analytics from './components/analytics/Analytics';
import theme from './theme';

function App() {
  return (
    <ChakraProvider theme={theme}>
      <CSSReset />
      <Router>
        <Box display="flex" minH="100vh">
          <Sidebar />
          <Box flex="1" ml="250px"> 
            <Navbar />
            <Box 
              as="main" 
              p={6}
              maxW="1600px"
              mx="auto"
              minH="calc(100vh - 64px)" 
            >
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/competitions/*" element={<Competitions />} />
                <Route path="/teams/*" element={<Teams />} />
                <Route path="/matches/*" element={<Matches />} />
                <Route path="/players/*" element={<Players />} />
                <Route path="/analytics/*" element={<Analytics />} />
              </Routes>
            </Box>
          </Box>
        </Box>
      </Router>
    </ChakraProvider>
  );
}

export default App;
