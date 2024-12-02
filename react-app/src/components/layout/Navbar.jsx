import {
  Box,
  Flex,
  IconButton,
  Input,
  InputGroup,
  InputLeftElement,
  useColorMode,
} from '@chakra-ui/react';
import { FiSearch, FiMoon, FiSun } from 'react-icons/fi';

function Navbar() {
  const { colorMode, toggleColorMode } = useColorMode();

  return (
    <Box
      as="nav"
      bg="white"
      borderBottom="1px"
      borderColor="gray.200"
      px={4}
      py={2}
      _dark={{
        bg: 'gray.800',
        borderColor: 'gray.700'
      }}
    >
      <Flex justify="space-between" align="center">
        <InputGroup maxW="400px">
          <InputLeftElement pointerEvents="none">
            <FiSearch />
          </InputLeftElement>
          <Input placeholder="Search..." />
        </InputGroup>

        <IconButton
          icon={colorMode === 'light' ? <FiMoon /> : <FiSun />}
          onClick={toggleColorMode}
          variant="ghost"
        />
      </Flex>
    </Box>
  );
}

export default Navbar;
