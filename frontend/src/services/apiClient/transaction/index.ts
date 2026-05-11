/**
 * Public entry for the transaction API client: re-exports {@link useTransactionAPIClient},
 * and request payload types used by callers.
 *
 * @module services/apiClient/transaction
 */

import { useTransactionAPIClient } from './client';

import type { TransactionPostRequest, TransactionPutRequest } from './types';

export { useTransactionAPIClient, type TransactionPostRequest, type TransactionPutRequest };
