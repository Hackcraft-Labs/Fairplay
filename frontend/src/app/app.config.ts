import { ApplicationConfig, provideBrowserGlobalErrorListeners, importProvidersFrom, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatIconModule } from '@angular/material/icon';
import { authInterceptor } from './core/interceptors/auth-interceptor';
import { errorInterceptor } from './core/interceptors/error-interceptor';

import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  	providers: [
		provideZoneChangeDetection({ eventCoalescing: true }),
    	provideBrowserGlobalErrorListeners(),
    	provideRouter(routes),
		provideHttpClient(withInterceptors([authInterceptor, errorInterceptor])),
		importProvidersFrom(
			MatSnackBarModule,
			MatIconModule
		)
  	]
};
