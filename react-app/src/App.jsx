import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ChakraProvider } from '@chakra-ui/react';
import theme from './theme';
import Layout from './components/layout/Layout';
import Dashboard from './components/Dashboard';
import CompetitionList from './components/competitions/CompetitionList';
import Competitions from './components/competitions/Competitions';
import Teams from './components/teams/Teams';
import Players from './components/players/Players';
import Matches from './components/matches/Matches';

function App() {
  return (
    <ChakraProvider theme={theme}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/competitions" element={<CompetitionList />} />
            <Route path="/competitions/:id/*" element={<Competitions />} />
            <Route path="/teams/*" element={<Teams />} />
            <Route path="/players/*" element={<Players />} />
            <Route path="/matches/*" element={<Matches />} />
          </Routes>
        </Layout>
      </Router>
    </ChakraProvider>
  );
}

export default App;
