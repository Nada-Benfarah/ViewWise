import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { FormsModule } from '@angular/forms';


@Component({
  selector: 'app-create-agent',
  standalone: true,
  imports: [CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatCheckboxModule],
  templateUrl: './create-agent.component.html',
  styleUrl: './create-agent.component.scss'
})
export class CreateAgentComponent {

 // Modèle de l'agent
 agent = {
  name: '',
  description: '',
  provider: '',
  model: '',
  instructions: '',
  conversationStarters: ''
};

// Méthode pour créer l'agent
createAgent() {
  console.log('Agent créé :', this.agent);
  // Ajoutez ici la logique pour enregistrer l'agent
}

// Méthode pour annuler la création
cancel() {
  console.log('Création annulée');
  // Ajoutez ici la logique pour annuler (par exemple, rediriger vers une autre page)
}
}
