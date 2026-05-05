/**
 * Shop list route: paginated shops table with category labels and navigation to each shop.
 *
 * Syncs the current page with the `page` query parameter, fetches shops via the shop API client
 * (loading state lives in the shop store), and loads categories once for id-to-name lookup.
 *
 * @module pages/shop/shopList/ShopList
 */

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Paper from '@mui/material/Paper';
import Skeleton from '@mui/material/Skeleton';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TablePagination from '@mui/material/TablePagination';
import TableRow from '@mui/material/TableRow';
import TableSortLabel from '@mui/material/TableSortLabel';
import Typography from '@mui/material/Typography';
import { useEffect, useMemo } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router';

import { Image } from '@components/image';
import { useShopAPIClient, useCategoryAPIClient } from '@services/apiClient';
import { useCategoryStore } from '@store/category';
import { useShopStore } from '@store/shop';

/**
 * Renders the shop catalog in a table with skeleton loading while the list request is in flight.
 *
 * @returns The shop list layout (loading skeleton or table with pagination).
 */
export function ShopList() {
  /** Fixed page size for shop list requests and MUI `TablePagination`. */
  const limit = 10;
  const navigate = useNavigate();
  const shops = useShopStore((state) => state.shops);
  const totalShops = useShopStore((state) => state.totalShops);
  const shopListLoading = useShopStore((state) => state.shopListLoading);
  const categories = useCategoryStore((state) => state.categories);
  const [searchParams, setSearchParams] = useSearchParams();

  const { getShops } = useShopAPIClient();
  const { getCategories } = useCategoryAPIClient();

  const columnHeaders = [
    {
      label: 'Name',
      key: 'name',
      isSortable: true,
    },
    {
      label: 'Category',
      key: 'category',
      isSortable: false,
    },
    {
      label: 'Description',
      key: 'description',
      isSortable: false,
    },
  ];

  /** Keep `page` in the URL, then fetch the matching slice of shops. */
  useEffect(() => {
    const pageRaw = searchParams.get('page');

    if (!pageRaw || !searchParams.get('sortBy') || !searchParams.get('sortOrder')) {
      setSearchParams((previous) => {
        if (!pageRaw) previous.set('page', '0');
        if (!searchParams.get('sortBy')) previous.set('sortBy', 'name');
        if (!searchParams.get('sortOrder')) previous.set('sortOrder', 'asc');
        return previous;
      });
    } else {
      const pageParsed = parseInt(pageRaw ?? '0', 10);
      const page = Number.isNaN(pageParsed) || pageParsed < 0 ? 0 : pageParsed;
      getShops(
        limit,
        page * limit,
        searchParams.get('sortBy') ?? undefined,
        searchParams.get('sortOrder') ?? undefined
      );
    }
  }, [searchParams]);

  /** Load category metadata once so table rows can resolve `categoryId` to a label. */
  useEffect(() => {
    if (categories === null) getCategories();
  }, [categories]);

  /** Map from category id to display name for table cells. */
  const groupedCategories = useMemo(() => {
    return Object.fromEntries(categories?.map((category) => [category.id, category.name]) ?? []);
  }, [categories]);

  if (shopListLoading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'end', mb: 2 }}>
          <Skeleton variant="rectangular" sx={{ width: '100px', height: '40px' }} />
        </Box>
        <Skeleton variant="rectangular" sx={{ width: '100%', height: '400px' }} />
      </Container>
    );
  }
  return (
    <Container maxWidth="lg" sx={{ mt: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'end', mb: 2 }}>
        <Button variant="contained" color="primary" onClick={() => navigate('/shop/create')}>
          <Typography variant="button">Create</Typography>
        </Button>
      </Box>
      <TableContainer component={Paper}>
        <Table sx={{ width: '100%' }} aria-label="simple table">
          <TableHead>
            {columnHeaders.map((header) => (
              <TableCell
                key={header.key}
                onClick={() => {
                  if (!header.isSortable) return;
                  setSearchParams((previous) => {
                    if (previous.get('sortBy') === header.key) {
                      previous.set(
                        'sortOrder',
                        previous.get('sortOrder') === 'asc' ? 'desc' : 'asc'
                      );
                    } else {
                      previous.set('sortBy', header.key);
                      previous.set('sortOrder', 'asc');
                    }
                    return previous;
                  });
                }}
              >
                <TableSortLabel
                  active={searchParams.get('sortBy') === header.key}
                  direction={searchParams.get('sortOrder') === 'asc' ? 'asc' : 'desc'}
                >
                  {header.label}
                </TableSortLabel>
              </TableCell>
            ))}
          </TableHead>
          <TableBody>
            {(shops ?? []).map((shop) => (
              <TableRow key={shop.id} sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                <TableCell component="th" scope="row">
                  <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                    <Image
                      src={shop.icon}
                      width="20px"
                      height="20px"
                      alt={`${shop.name} shop icon`}
                    />
                    <Link
                      to={`/shop/${shop.id}`}
                      style={{
                        textDecoration: 'none',
                        color: '#023e8a',
                        fontWeight: 'bold',
                        marginLeft: '0.25rem',
                      }}
                    >
                      {shop.name}
                    </Link>
                  </Box>
                </TableCell>
                <TableCell align="left">{groupedCategories[shop.categoryId as number]}</TableCell>
                <TableCell align="left">{shop.description}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={totalShops}
          rowsPerPage={limit}
          page={parseInt(searchParams.get('page') ?? '0')}
          onPageChange={(_, page) => setSearchParams({ page: page.toString() })}
          rowsPerPageOptions={[]}
        />
      </TableContainer>
    </Container>
  );
}
