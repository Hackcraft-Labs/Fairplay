import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { catchError, throwError } from 'rxjs';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
	const snackBar = inject(MatSnackBar);

	return next(req).pipe(
		catchError((error: unknown) => {
		let message = 'An unexpected error occurred.';

		if (error instanceof HttpErrorResponse) {
			message =
			error.error?.detail ||
			error.error?.message ||
			`Request failed with status ${error.status}`;
		}

		snackBar.open(message, 'Dismiss', {
			duration: 5000,
			panelClass: ['fp-snackbar-error']
		});

		return throwError(() => error);
		})
	);
};