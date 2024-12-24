import React from 'react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import {
  Box,
  Container,
  Flex,
  IconButton,
  Input,
  InputGroup,
  InputLeftElement,
  useColorMode,
  Link,
  HStack,
  Text,
} from '@chakra-ui/react';
import { FiSearch, FiMoon, FiSun } from 'react-icons/fi';

function Navbar() {
  const { colorMode, toggleColorMode } = useColorMode();
  const location = useLocation();

  const navItems = [
    { label: 'Dashboard', path: '/' },
    { label: 'Teams', path: '/teams' },
    { label: 'Players', path: '/players' },
    { label: 'Matches', path: '/matches' },
    { label: 'Standings', path: '/standings' },
    { label: 'Analytics', path: '/analytics' },
  ];

  return (
    <Box
      as="nav"
      bg={colorMode === 'light' ? 'white' : 'gray.800'}
      py={4}
      borderBottom="1px"
      borderColor={colorMode === 'light' ? 'gray.200' : 'gray.700'}
    >
      <Container maxW="container.xl">
        <Flex justify="space-between" align="center">
          <Text fontSize="xl" fontWeight="bold" color="brand.500">
            Football Analytics
          </Text>

          <HStack spacing={8}>
            {navItems.map((item, index) => (
              <Link
                key={index}
                as={RouterLink}
                to={item.path}
                px={3}
                py={2}
                rounded="md"
                color={colorMode === 'light' ? 'gray.700' : 'gray.300'}
                _hover={{
                  textDecoration: 'none',
                  bg: colorMode === 'light' ? 'gray.100' : 'gray.700',
                  color: colorMode === 'light' ? 'brand.500' : 'white',
                }}
                bg={location.pathname === item.path ? (colorMode === 'light' ? 'gray.100' : 'gray.700') : 'transparent'}
                fontWeight={location.pathname === item.path ? 'bold' : 'medium'}
                borderBottom={location.pathname === item.path ? '2px' : '0'}
                borderColor="brand.500"
              >
                {item.label}
              </Link>
            ))}
          </HStack>

          <HStack spacing={4}>
            <InputGroup maxW="300px" display={{ base: 'none', md: 'block' }}>
              <InputLeftElement pointerEvents="none">
                <FiSearch color={colorMode === 'light' ? 'gray.400' : 'gray.600'} />
              </InputLeftElement>
              <Input 
                placeholder="Search..." 
                variant="filled"
                _placeholder={{ color: colorMode === 'light' ? 'gray.400' : 'gray.600' }}
              />
            </InputGroup>

            <IconButton
              icon={colorMode === 'light' ? <FiMoon /> : <FiSun />}
              onClick={toggleColorMode}
              variant="ghost"
              aria-label="Toggle color mode"
              color={colorMode === 'light' ? 'gray.700' : 'gray.300'}
            />
          </HStack>
        </Flex>
      </Container>
    </Box>
  );
}

export default Navbar;
