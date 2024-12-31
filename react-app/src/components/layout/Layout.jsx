import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box, Container, useColorModeValue } from '@chakra-ui/react';
import Navbar from './Navbar';

function Layout() {
  const bg = useColorModeValue('white', 'gray.800');
  
  return (
    <Box minH="100vh" bg={bg}>
      <Navbar />
      <Container maxW="container.xl" py={8}>
        <Outlet />
      </Container>
    </Box>
  );
}

export default Layout;
