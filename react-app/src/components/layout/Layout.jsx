import { Box } from '@chakra-ui/react';
import Navbar from './Navbar';
import Sidebar from './Sidebar';

function Layout({ children }) {
  return (
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
          {children}
        </Box>
      </Box>
    </Box>
  );
}

export default Layout;
