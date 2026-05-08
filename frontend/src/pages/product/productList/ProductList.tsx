/**
 * Product list route: paginated products table with category labels and navigation to each product.
 *
 * Syncs the current page with the `page` query parameter, fetches products into local component
 * state, and loads categories once for id-to-name lookup.
 *
 * @module pages/product/productList/ProductList
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
import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router';

import { Search } from '@components/search';
import { useCategoryAPIClient } from '@services/apiClient';
import { fetchProducts } from '@services/apiClient/product';
import { useCategoryStore } from '@store/category';
import type { ProductSimpleType } from '@store/product';

/**
 * Renders the product catalog in a table with skeleton loading while the list request is in flight.
 *
 * @returns The product list layout (loading skeleton or table with pagination).
 */
export function ProductList() {
  /** Fixed page size for product list requests and MUI `TablePagination`. */
  const limit = 10;
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

  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const [products, setProducts] = useState<ProductSimpleType[] | null>(null);
  const [totalProducts, setTotalProducts] = useState<number>(0);

  const categories = useCategoryStore((state) => state.categories);

  const { getCategories } = useCategoryAPIClient();

  /** Keep `page` in the URL, then fetch the matching slice of products. */
  useEffect(() => {
    const pageRaw = searchParams.get('page');

    if (!pageRaw || !searchParams.get('sortBy') || !searchParams.get('sortOrder')) {
      setSearchParams((previous) => {
        if (!pageRaw) previous.set('page', '0');
        if (!searchParams.get('sortBy')) previous.set('sortBy', 'name');
        if (!searchParams.get('sortOrder')) previous.set('sortOrder', 'asc');
        return previous;
      });
      return;
    }

    const pageParsed = parseInt(pageRaw ?? '0', limit);
    const page = Number.isNaN(pageParsed) || pageParsed < 0 ? 0 : pageParsed;
    const filters = searchParams.get('search')
      ? [{ column: 'name', operator: 'ilike', value: searchParams.get('search') }]
      : undefined;

    // Guard against out-of-order responses when params change faster than the network.
    let cancelled = false;
    fetchProducts(
      limit,
      page * limit,
      searchParams.get('sortBy') ?? undefined,
      searchParams.get('sortOrder') ?? undefined,
      filters
    ).then(({ data, total }) => {
      if (cancelled) return;
      setProducts(data);
      setTotalProducts(total);
    });
    return () => {
      cancelled = true;
    };
  }, [searchParams]);

  /** Load category metadata once so table rows can resolve `categoryId` to a label. */
  useEffect(() => {
    if (categories === null) getCategories();
  }, [categories]);

  /** Map from category id to display name for table cells. */
  const groupedCategories = useMemo(() => {
    return Object.fromEntries(categories?.map((category) => [category.id, category.name]) ?? []);
  }, [categories]);

  if (products === null) {
    return (
      <Container maxWidth="lg" sx={{ mt: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Skeleton variant="rectangular" sx={{ width: '300px', height: '40px' }} />
          <Skeleton variant="rectangular" sx={{ width: '100px', height: '40px' }} />
        </Box>
        <Skeleton variant="rectangular" sx={{ width: '100%', height: '600px' }} />
      </Container>
    );
  }
  return (
    <Container maxWidth="lg" sx={{ mt: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Search label="Search by name" />
        <Button variant="contained" color="primary" onClick={() => navigate('/product/create')}>
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
            {(products ?? []).map((product) => (
              <TableRow key={product.id} sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                <TableCell component="th" scope="row">
                  <Link
                    to={`/product/${product.id}`}
                    style={{
                      textDecoration: 'none',
                      color: '#023e8a',
                      fontWeight: 'bold',
                      marginLeft: '0.25rem',
                    }}
                  >
                    {product.name}
                  </Link>
                </TableCell>
                <TableCell align="left">
                  {groupedCategories[product.categoryId as number]}
                </TableCell>
                <TableCell align="left">{product.description}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={totalProducts}
          rowsPerPage={limit}
          page={parseInt(searchParams.get('page') ?? '0')}
          onPageChange={(_, page) => setSearchParams({ page: page.toString() })}
          rowsPerPageOptions={[]}
        />
      </TableContainer>
    </Container>
  );
}
