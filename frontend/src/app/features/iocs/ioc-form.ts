import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { IocService } from '../../core/services/ioc';
import { Ioc } from '../../core/models/ioc';
import { CardComponent } from '../../shared/components/card/card';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner';

@Component({
	selector: 'fp-ioc-form',
	standalone: true,
	imports: [
		CommonModule,
		ReactiveFormsModule,
		RouterModule,
		MatFormFieldModule,
		MatInputModule,
		MatButtonModule,
		MatSlideToggleModule,
		CardComponent,
		LoadingSpinnerComponent
	],
	templateUrl: './ioc-form.html',
	styleUrl: './ioc-form.scss'
})
export class IocFormComponent implements OnInit {
	private readonly fb = inject(FormBuilder);
	private readonly route = inject(ActivatedRoute);
	private readonly router = inject(Router);
	private readonly iocService = inject(IocService);

	loading = false;
	isEditMode = false;

	form = this.fb.group({
		name: ['', [Validators.required]],
		file_hash: ['', [Validators.required]],
		poll_time: [60, [Validators.required, Validators.min(1)]],
		active: [true]
	});

	get nameParam(): string | null {
		return this.route.snapshot.paramMap.get('name');
	}

	ngOnInit(): void {
		const existingName = this.nameParam;
		this.isEditMode = existingName !== null && existingName !== 'new';

		if (this.isEditMode && existingName) {
			this.loading = true;
			this.iocService.get(existingName).subscribe({
				next: ioc => {
					this.form.patchValue({
						name: ioc.name,
						file_hash: ioc.file_hash,
						poll_time: ioc.poll_time ?? 60,
						active: ioc.active !== false
					});
					this.loading = false;
				},
				error: () => {
					this.loading = false;
					this.router.navigate(['/iocs']);
				}
			});
		}
	}

	submit(): void {
		if (this.form.invalid) {
			this.form.markAllAsTouched();
			return;
		}

		const v = this.form.value;
		const payload: Ioc = {
			name: v.name!,
			file_hash: v.file_hash!,
			poll_time: Number(v.poll_time) || 60,
			active: v.active ?? true
		};

		this.loading = true;

		if (this.isEditMode && this.nameParam) {
			this.iocService.update(this.nameParam, payload).subscribe({
				next: ioc => this.router.navigate(['/iocs', ioc.name]),
				error: () => (this.loading = false)
			});
		} else {
			this.iocService.create(payload).subscribe({
				next: ioc => this.router.navigate(['/iocs', ioc.name]),
				error: () => (this.loading = false)
			});
		}
	}
}
