<template>
  <div class="container py-2">
    <h3>Set a new goal</h3>

    <form @submit.prevent="createGoal" class="form mb-2">
      <div class="form-group">
        <label for="goal-name">Name (Required)</label>
        <input id="goal-name" type="text" required class="form-control" v-model="newGoal.name">
      </div>

      <div class="form-group">
        <label for="goal-target">Target (Required)</label>
        <input id="goal-target" type="text" required class="form-control" v-model="newGoal.target">
      </div>

      <div class="form-group">
        <label for="goal-target-criteria">Target criteria</label>
        <b-form-select id="goal-target-criteria" v-model="newGoal.target_match">
          <option value="eq">Equal</option>
          <option value="prefix">Prefix match</option>
          <option value="regex">Regular expression match</option>
        </b-form-select>
      </div>

      <div class="form-group">
        <label for="goal-path">Path</label>
        <input id="goal-path" type="text" class="form-control" v-model="newGoal.path">
      </div>

      <div class="form-group">
        <label for="goal-path-criteria">Path criteria</label>
        <b-form-select id="goal-path-criteria" v-model="newGoal.path_match">
          <option value="eq">Equal</option>
          <option value="prefix">Prefix match</option>
          <option value="regex">Regular expression match</option>
        </b-form-select>
      </div>

      <div class="form-group">
        <label for="goal-label">Label</label>
        <input id="goal-label" type="text" class="form-control" v-model="newGoal.label">
      </div>

      <div class="form-group">
        <label for="goal-label-criteria">Label criteria</label>
        <b-form-select id="goal-label-criteria" v-model="newGoal.label_match">
          <option value="eq">Equal</option>
          <option value="prefix">Prefix match</option>
          <option value="regex">Regular expression match</option>
        </b-form-select>
      </div>

      <button type="submit" class="btn btn-primary">Create</button>
    </form>

    <h3>Goals</h3>
    <div class="row">
      <div v-for="goal in goals" :key="goal.id" class="col-6">
        <goal-result-card :goal="goal" @delete="reloadGoals"/>
      </div>
    </div>
  </div>
</template>

<script>
  import urlparser from 'url'
  import GoalResultCard from '../components/GoalResultCard'

  const goalDefault = (url = null, target = null, label = null) => {
    let path = null
    if (url) {
      path = urlparser.parse(url).path
    }


    return {
      name: null,
      target: target,
      target_match: 'eq',
      path: path,
      path_match: 'eq',
      label: label,
      label_match: 'eq'
    }
  }
  export default {
    components: {GoalResultCard},
    data() {
      return {
        newGoal: goalDefault(this.$route.query.url, this.$route.query.target, this.$route.query.label),
        goals: []
      }
    },
    async created() {
      await this.reloadGoals()
    },
    methods: {
      async reloadGoals() {
        const name = this.$route.params.name
        const goals = await this.$Amplify.API.get('OTMClientAPI', `/orgs/${this.$route.params.org}/containers/${name}/goals`)
        this.goals = goals
      },
      async createGoal() {
        const name = this.$route.params.name
        await this.$Amplify.API.post('OTMClientAPI', `/orgs/${this.$route.params.org}/containers/${name}/goals`, {body: this.newGoal})
        this.newGoal = goalDefault()
        await this.reloadGoals()
      }
    }
  }
</script>

<style scoped>
  .form {
    max-width: 500px;
  }
</style>
